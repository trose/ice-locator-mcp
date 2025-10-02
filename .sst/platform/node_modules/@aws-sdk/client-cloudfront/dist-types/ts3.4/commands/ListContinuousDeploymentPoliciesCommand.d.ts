import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  ListContinuousDeploymentPoliciesRequest,
  ListContinuousDeploymentPoliciesResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListContinuousDeploymentPoliciesCommandInput
  extends ListContinuousDeploymentPoliciesRequest {}
export interface ListContinuousDeploymentPoliciesCommandOutput
  extends ListContinuousDeploymentPoliciesResult,
    __MetadataBearer {}
export declare class ListContinuousDeploymentPoliciesCommand extends $Command<
  ListContinuousDeploymentPoliciesCommandInput,
  ListContinuousDeploymentPoliciesCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListContinuousDeploymentPoliciesCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListContinuousDeploymentPoliciesCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    ListContinuousDeploymentPoliciesCommandInput,
    ListContinuousDeploymentPoliciesCommandOutput
  >;
  private serialize;
  private deserialize;
}
