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
  CreateContinuousDeploymentPolicyRequest,
  CreateContinuousDeploymentPolicyResult,
} from "../models/models_0";
export { __MetadataBearer, $Command };
export interface CreateContinuousDeploymentPolicyCommandInput
  extends CreateContinuousDeploymentPolicyRequest {}
export interface CreateContinuousDeploymentPolicyCommandOutput
  extends CreateContinuousDeploymentPolicyResult,
    __MetadataBearer {}
export declare class CreateContinuousDeploymentPolicyCommand extends $Command<
  CreateContinuousDeploymentPolicyCommandInput,
  CreateContinuousDeploymentPolicyCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: CreateContinuousDeploymentPolicyCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: CreateContinuousDeploymentPolicyCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    CreateContinuousDeploymentPolicyCommandInput,
    CreateContinuousDeploymentPolicyCommandOutput
  >;
  private serialize;
  private deserialize;
}
