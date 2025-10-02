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
  GetContinuousDeploymentPolicyRequest,
  GetContinuousDeploymentPolicyResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetContinuousDeploymentPolicyCommandInput
  extends GetContinuousDeploymentPolicyRequest {}
export interface GetContinuousDeploymentPolicyCommandOutput
  extends GetContinuousDeploymentPolicyResult,
    __MetadataBearer {}
export declare class GetContinuousDeploymentPolicyCommand extends $Command<
  GetContinuousDeploymentPolicyCommandInput,
  GetContinuousDeploymentPolicyCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetContinuousDeploymentPolicyCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetContinuousDeploymentPolicyCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    GetContinuousDeploymentPolicyCommandInput,
    GetContinuousDeploymentPolicyCommandOutput
  >;
  private serialize;
  private deserialize;
}
