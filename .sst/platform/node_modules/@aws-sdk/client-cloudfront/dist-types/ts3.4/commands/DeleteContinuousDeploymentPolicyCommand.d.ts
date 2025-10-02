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
import { DeleteContinuousDeploymentPolicyRequest } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface DeleteContinuousDeploymentPolicyCommandInput
  extends DeleteContinuousDeploymentPolicyRequest {}
export interface DeleteContinuousDeploymentPolicyCommandOutput
  extends __MetadataBearer {}
export declare class DeleteContinuousDeploymentPolicyCommand extends $Command<
  DeleteContinuousDeploymentPolicyCommandInput,
  DeleteContinuousDeploymentPolicyCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: DeleteContinuousDeploymentPolicyCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: DeleteContinuousDeploymentPolicyCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    DeleteContinuousDeploymentPolicyCommandInput,
    DeleteContinuousDeploymentPolicyCommandOutput
  >;
  private serialize;
  private deserialize;
}
